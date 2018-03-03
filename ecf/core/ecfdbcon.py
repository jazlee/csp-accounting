import tools
import sqlalchemy as sa
import elixir

__all__ = ('configure')

db_engine = None
db_opts = {}

def configure(opts=None):
  global db_engine, db_opts
  url = tools.config['ecfserver.dbconnection.url']
  db_opts = opts or {}
  # db_opts['strategy'] = 'threadlocal'
  # db_opts['poolclass'] = sa.pool.SingletonThreadPool
  db_opts['strategy'] = 'threadlocal'
  db_opts['pool_size'] = 16
  db_opts['pool_recycle'] = 900
  if url.find('sqlite') < 0:
    db_opts['max_overflow'] = 32
  db_opts['echo'] = False
  db_opts['echo_pool'] = False
  db_engine = sa.create_engine(url, **db_opts)
  elixir.metadata.bind = db_engine
  elixir.setup_all(True, checkfirst=True)

