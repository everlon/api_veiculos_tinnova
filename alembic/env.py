import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    fileConfig(config.config_file_name) # type: ignore[arg-type]

# Obter a URL do banco de dados a partir de variáveis de ambiente
# ou usar o valor do alembic.ini como fallback (ou padrão)
db_user = os.getenv("DB_USER_ALEMBIC", "root")
db_password = os.getenv("DB_PASSWORD_ALEMBIC", "root")
db_host = os.getenv("DB_HOST_ALEMBIC", "db")
db_port = os.getenv("DB_PORT_ALEMBIC", "3306")
db_name = os.getenv("DB_NAME_ALEMBIC", "tinnova_db") # ou o nome do DB que alembic deve usar

config.set_main_option("sqlalchemy.url", f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# Importar a base declarativa e os modelos
import sys
import os
sys.path.append(os.getcwd())
from app.models.veiculo import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired here by fair game. e.g.:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a database lookups to exist.

    Calls to context.execute() go to the run_sync
    per above.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Usar variáveis de ambiente para conectar ao banco de dados no Docker
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    # Fallback para a URL do ini se as variáveis de ambiente não estiverem definidas
    # Isso é útil para rodar migrações fora do Docker se necessário
    if not all([db_user, db_password, db_host, db_port, db_name]):
        print("WARNING: Variáveis de ambiente do banco de dados não definidas. Usando URL do alembic.ini")
        # Obtém a URL do alembic.ini como fallback
        url = config.get_main_option("sqlalchemy.url")
        if url is None:
             raise ValueError("SQLALCHEMY_DATABASE_URL não configurada.")
    else:
        url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    connectable = engine_from_config(
        {},
        url=url,
        prefix="",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        try:
            # Adiciona a configuração do storage engine para MySQL
            context.execute("SET default_storage_engine=InnoDB")
            with context.begin_transaction():
                context.run_migrations()
        finally:
            connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
