"""convert_enum_values_to_russian

Revision ID: 1d4a14dd5c28
Revises: 933ade9f4842
Create Date: 2025-12-07 11:31:22.766148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d4a14dd5c28'
down_revision: Union[str, None] = '933ade9f4842'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert existing enum values from English to Russian."""
    
    # Update ResourceType enum values
    op.execute("""
        UPDATE water_objects 
        SET resource_type = CASE resource_type
            WHEN 'lake' THEN 'озеро'
            WHEN 'canal' THEN 'канал'
            WHEN 'reservoir' THEN 'водохранилище'
            WHEN 'river' THEN 'река'
            WHEN 'other' THEN 'другое'
            ELSE resource_type
        END
    """)
    
    # Update WaterType enum values
    op.execute("""
        UPDATE water_objects 
        SET water_type = CASE water_type
            WHEN 'fresh' THEN 'пресная'
            WHEN 'non_fresh' THEN 'непресная'
            ELSE water_type
        END
        WHERE water_type IS NOT NULL
    """)
    
    # Update FaunaType enum values
    op.execute("""
        UPDATE water_objects 
        SET fauna = CASE fauna
            WHEN 'fish_bearing' THEN 'рыбопродуктивная'
            WHEN 'non_fish_bearing' THEN 'нерыбопродуктивная'
            ELSE fauna
        END
        WHERE fauna IS NOT NULL
    """)
    
    # Update PriorityLevel enum values
    op.execute("""
        UPDATE water_objects 
        SET priority_level = CASE priority_level
            WHEN 'high' THEN 'высокий'
            WHEN 'medium' THEN 'средний'
            WHEN 'low' THEN 'низкий'
            ELSE priority_level
        END
    """)


def downgrade() -> None:
    """Revert enum values back to English."""
    
    # Revert ResourceType enum values
    op.execute("""
        UPDATE water_objects 
        SET resource_type = CASE resource_type
            WHEN 'озеро' THEN 'lake'
            WHEN 'канал' THEN 'canal'
            WHEN 'водохранилище' THEN 'reservoir'
            WHEN 'река' THEN 'river'
            WHEN 'другое' THEN 'other'
            ELSE resource_type
        END
    """)
    
    # Revert WaterType enum values
    op.execute("""
        UPDATE water_objects 
        SET water_type = CASE water_type
            WHEN 'пресная' THEN 'fresh'
            WHEN 'непресная' THEN 'non_fresh'
            ELSE water_type
        END
        WHERE water_type IS NOT NULL
    """)
    
    # Revert FaunaType enum values
    op.execute("""
        UPDATE water_objects 
        SET fauna = CASE fauna
            WHEN 'рыбопродуктивная' THEN 'fish_bearing'
            WHEN 'нерыбопродуктивная' THEN 'non_fish_bearing'
            ELSE fauna
        END
        WHERE fauna IS NOT NULL
    """)
    
    # Revert PriorityLevel enum values
    op.execute("""
        UPDATE water_objects 
        SET priority_level = CASE priority_level
            WHEN 'высокий' THEN 'high'
            WHEN 'средний' THEN 'medium'
            WHEN 'низкий' THEN 'low'
            ELSE priority_level
        END
    """)
