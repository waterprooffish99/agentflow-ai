import sys
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Base
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

def format_type(col_type):
    if isinstance(col_type, postgresql.UUID):
        return "postgresql.UUID(as_uuid=True)"
    if isinstance(col_type, postgresql.JSONB):
        return "postgresql.JSONB(as_uuid=False)" # JSONB doesn't have as_uuid, but postgresql.JSONB is fine
    
    # Generic fallback
    type_name = type(col_type).__name__
    if type_name == "DateTime":
        return "sa.DateTime(timezone=True)"
    if type_name == "String":
        return f"sa.String(length={col_type.length})"
    if type_name == "Boolean":
        return "sa.Boolean()"
    if type_name == "Integer":
        return "sa.Integer()"
    if type_name == "Numeric":
        return f"sa.Numeric(precision={col_type.precision}, scale={col_type.scale})"
    if type_name == "Text":
        return "sa.Text()"
    
    return f"sa.{type_name}()"

def generate_migration():
    print('"""initial schema')
    print()
    print('Revision ID: 0001_initial_schema')
    print('Revises:')
    print('Create Date: 2026-05-12')
    print('"""')
    print()
    print('from alembic import op')
    print('import sqlalchemy as sa')
    print('from sqlalchemy.dialects import postgresql')
    print()
    print('revision = "0001_initial_schema"')
    print('down_revision = None')
    print('branch_labels = None')
    print('depends_on = None')
    print()
    print('def upgrade() -> None:')
    
    for table in Base.metadata.sorted_tables:
        print(f'    op.create_table(')
        print(f'        "{table.name}",')
        for column in table.columns:
            col_args = [f'"{column.name}"', format_type(column.type)]
            
            if column.primary_key:
                col_args.append("primary_key=True")
            if not column.nullable:
                col_args.append("nullable=False")
            if column.default is not None and not callable(column.default.arg):
                # Simple default value
                val = column.default.arg
                if isinstance(val, str):
                    val = f"'{val}'"
                col_args.append(f"server_default=sa.text({val})")
            
            # Foreign keys
            for fk in column.foreign_keys:
                col_args.append(f'sa.ForeignKey("{fk.target_fullname}", ondelete="{fk.ondelete or "CASCADE"}")')
            
            print(f'        sa.Column({", ".join(col_args)}),')
        
        # Table args like Index
        for arg in table.indexes:
            cols = ", ".join([f'"{c.name}"' for c in arg.columns])
            print(f'        sa.Index("{arg.name}", {cols}, unique={arg.unique}),')
            
        print(f'    )')
        print()

    print('def downgrade() -> None:')
    for table in reversed(Base.metadata.sorted_tables):
        print(f'    op.drop_table("{table.name}")')

if __name__ == "__main__":
    generate_migration()
