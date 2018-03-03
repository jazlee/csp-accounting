import struct

_FB_MAX_ENTITY_NAME_LENGTH = 32
_MAX_ARRAY_DIMENSIONS = 16

def look_up_array_descriptor(con, relName, fieldName):
    return _loadArrayFieldCacheEntry(con, relName, fieldName)[0]

def look_up_array_subtype(con, relName, fieldName):
    return _loadArrayFieldCacheEntry(con, relName, fieldName)[1]

# Supporting code:
def _loadArrayFieldCacheEntry(con, relName, fieldName):
    # Given a connection and a 2-tuple of (relation name, field name) for an
    # array field, create and return an array descriptor for that field.
    # For a given field and connection, the descriptor is created only once,
    # then cached for all future lookups.

    fieldKey = (relName, fieldName)

    arrayFieldMetaCache = getattr(con, '_array_field_meta_cache', None)
    if arrayFieldMetaCache is not None:
        entry = arrayFieldMetaCache.get(fieldKey, None)
        if entry is not None:
            # Cache hit:
            return entry
    else:
        con._array_field_meta_cache = {}

    # Cache miss:
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT "
            # These fields aren't placed directly in the descriptor:
            " FIELD_SPEC.RDB$FIELD_NAME,"       # internal field name
            " FIELD_SPEC.RDB$FIELD_SUB_TYPE,"   # field subtype
            # These fields are placed directly in the descriptor:
            " FIELD_SPEC.RDB$FIELD_TYPE,"       # array_desc_dtype
            " FIELD_SPEC.RDB$FIELD_SCALE,"      # array_desc_scale
            " FIELD_SPEC.RDB$FIELD_LENGTH,"     # array_desc_length
            " FIELD_SPEC.RDB$DIMENSIONS "       # array_desc_dimensions
            "FROM "
                   "RDB$FIELDS FIELD_SPEC "
              "JOIN RDB$RELATION_FIELDS REL_FIELDS "
                "ON FIELD_SPEC.RDB$FIELD_NAME = REL_FIELDS.RDB$FIELD_SOURCE "
            "WHERE "
                  "REL_FIELDS.RDB$RELATION_NAME = ? "
              "AND REL_FIELDS.RDB$FIELD_NAME = ?",
            (relName, fieldName)
          )

        basicSpecs = cur.fetchone()
        assert basicSpecs is not None

        cur.execute(
            "SELECT RDB$LOWER_BOUND, RDB$UPPER_BOUND "
            "FROM RDB$FIELD_DIMENSIONS "
            "WHERE RDB$FIELD_NAME = ? "
            "ORDER BY RDB$DIMENSION",
            (basicSpecs[0],)
          )

        boundsForEachDimension = cur.fetchall()
        assert boundsForEachDimension
    finally:
        cur.close()

    # Flatten boundsForEachDimension:
    cBoundsSource = []
    for lowerBound, upperBound in boundsForEachDimension:
        cBoundsSource.append(lowerBound)
        cBoundsSource.append(upperBound)

    desc = _createArrayDescriptor(
        basicSpecs[2], basicSpecs[3], basicSpecs[4], fieldName, relName,
        basicSpecs[5], cBoundsSource
      )

    subType = basicSpecs[1]

    cacheEntry = (desc, subType)
    con._array_field_meta_cache[fieldKey] = cacheEntry
    return cacheEntry

_FMT__ISC_ARRAY_DESC = (
    'B'    # unsigned char     array_desc_dtype
    'b'    # char              array_desc_scale
    'H'    # unsigned short    array_desc_length
    + str(_FB_MAX_ENTITY_NAME_LENGTH) + 's'
           # char              array_desc_field_name[_FB_MAX_ENTITY_NAME_LENGTH]
    + str(_FB_MAX_ENTITY_NAME_LENGTH) + 's'
           # char              array_desc_relation_name[_FB_MAX_ENTITY_NAME_LENGTH]
    'h'    # short             array_desc_dimensions
    'h'    # short             array_desc_flags
    + str(_MAX_ARRAY_DIMENSIONS * 2) + 'h'
           # ISC_ARRAY_BOUND   array_desc_bounds[16]
           #  (an ISC_ARRAY_BOUND consists of two shorts)
  )

def _createArrayDescriptor(array_desc_dtype, array_desc_scale,
    array_desc_length, array_desc_field_name, array_desc_relation_name,
    array_desc_dimensions, array_desc_bounds,
  ):
    array_desc_field_name = _padEntityName(array_desc_field_name)
    array_desc_relation_name = _padEntityName(array_desc_relation_name)

    if len(array_desc_bounds) < _MAX_ARRAY_DIMENSIONS * 2:
        array_desc_bounds += [0] * (_MAX_ARRAY_DIMENSIONS * 2 - len(array_desc_bounds))
    assert len(array_desc_bounds) == _MAX_ARRAY_DIMENSIONS * 2

    packArgs = [
        array_desc_dtype , array_desc_scale, array_desc_length,
        array_desc_field_name, array_desc_relation_name,
        array_desc_dimensions,
        0, # array_desc_flags is always zero initially
      ] + array_desc_bounds
    return struct.pack(_FMT__ISC_ARRAY_DESC, *packArgs)

def _padEntityName(en):
    en = en.strip()
    en_len = len(en)
    assert en_len <= _FB_MAX_ENTITY_NAME_LENGTH
    return en  + ((_FB_MAX_ENTITY_NAME_LENGTH - en_len) * '\0')
