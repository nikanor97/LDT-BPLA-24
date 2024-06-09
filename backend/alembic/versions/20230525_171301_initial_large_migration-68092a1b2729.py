"""initial_large_migration

Revision ID: 68092a1b2729
Revises: 
Create Date: 2023-05-25 17:13:01.719446

"""
from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68092a1b2729'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    try:
        globals()["upgrade_%s" % engine_name]()
    except KeyError:
        pass


def downgrade(engine_name: str) -> None:
    try:
        globals()["downgrade_%s" % engine_name]()
    except KeyError:
        pass





def upgrade_projects() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('projects',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('status', sa.Enum('created', 'in_progress', 'finished', name='projectstatusoption'), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deadline_at', sa.Date(), nullable=True),
        sa.Column('document_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_table('apartments',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('status', sa.Enum('created', 'in_progress', 'approved', 'declined', name='apartmentstatusoption'), nullable=True),
        sa.Column('number', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('decoration_type', sa.Enum('rough', 'finishing', name='apartmentdecorationtypeoption'), nullable=True),
        sa.Column('building', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('section', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('floor', sa.Integer(), nullable=True),
        sa.Column('rooms_total', sa.Integer(), nullable=True),
        sa.Column('square', sa.Numeric(), nullable=True),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('labels',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('color', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'project_id', name='name_project_id_constr')
    )
    op.create_index(op.f('ix_labels_name'), 'labels', ['name'], unique=False)
    op.create_index(op.f('ix_labels_project_id'), 'labels', ['project_id'], unique=False)
    op.create_table('project_documents',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('apt_count', sa.Integer(), nullable=True),
        sa.Column('n_finishing', sa.Integer(), nullable=True),
        sa.Column('n_rough', sa.Integer(), nullable=True),
        sa.Column('source_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_roles',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('role_type', sa.Enum('author', 'view_only', 'verificator', name='roletypeoption'), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_project_role', 'user_roles', ['user_id', 'project_id', 'role_type'], unique=True)
    op.create_index(op.f('ix_user_roles_project_id'), 'user_roles', ['project_id'], unique=False)
    op.create_index(op.f('ix_user_roles_user_id'), 'user_roles', ['user_id'], unique=False)
    op.create_table('videos',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('status', sa.Enum('created', 'extracted', 'approved', 'declined', name='videostatusoption'), nullable=True),
        sa.Column('length_sec', sa.Numeric(), nullable=True),
        sa.Column('n_frames', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('source_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('owner_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('apartment_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['apartment_id'], ['apartments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('frames',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('frame_offset', sa.Integer(), nullable=False),
        sa.Column('video_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_frame_video_id_frame_offset', 'frames', ['video_id', 'frame_offset'], unique=True)
    op.create_table('frame_markup',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('frame_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('label_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('confidence', sa.Numeric(), nullable=True),
        sa.Column('coord_top_left_x', sa.Numeric(), nullable=True),
        sa.Column('coord_top_left_y', sa.Numeric(), nullable=True),
        sa.Column('coord_bottom_right_x', sa.Numeric(), nullable=True),
        sa.Column('coord_bottom_right_y', sa.Numeric(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['frame_id'], ['frames.id'], ),
        sa.ForeignKeyConstraint(['label_id'], ['labels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('verification_tags',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('tagname', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('groupname', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tagname_groupname', 'verification_tags', ['tagname', 'groupname'], unique=True)
    op.create_table('project_tags',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('tag_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['verification_tags.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'tag_id', name='project_tag_constr')
    )
    op.create_index(op.f('ix_project_tags_project_id'), 'project_tags', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_tags_tag_id'), 'project_tags', ['tag_id'], unique=False)
    # ### end Alembic commands ###


def downgrade_projects() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('frame_markup')
    op.drop_index('idx_frame_video_id_frame_offset', table_name='frames')
    op.drop_table('frames')
    op.drop_table('videos')
    op.drop_index(op.f('ix_user_roles_user_id'), table_name='user_roles')
    op.drop_index(op.f('ix_user_roles_project_id'), table_name='user_roles')
    op.drop_index('idx_user_project_role', table_name='user_roles')
    op.drop_table('user_roles')
    op.drop_table('project_documents')
    op.drop_index(op.f('ix_labels_project_id'), table_name='labels')
    op.drop_index(op.f('ix_labels_name'), table_name='labels')
    op.drop_table('labels')
    op.drop_table('apartments')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_project_tags_tag_id'), table_name='project_tags')
    op.drop_index(op.f('ix_project_tags_project_id'), table_name='project_tags')
    op.drop_table('project_tags')
    op.drop_index('idx_tagname_groupname', table_name='verification_tags')
    op.drop_table('verification_tags')
    op.drop_table('projects')
    # ### end Alembic commands ###
    op.execute("""DROP TYPE projectstatusoption""")
    op.execute("""DROP TYPE apartmentdecorationtypeoption""")
    op.execute("""DROP TYPE roletypeoption""")
    op.execute("""DROP TYPE videostatusoption""")
    op.execute("""DROP TYPE apartmentstatusoption""")



def upgrade_users() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)
    op.create_table('user_passwords',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_passwords_user_id'), 'user_passwords', ['user_id'], unique=False)
    op.create_table('user_tokens',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.Column('access_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('refresh_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('token_type', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('access_expires_at', sa.DateTime(), nullable=False),
        sa.Column('refresh_expires_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_tokens_user_id'), 'user_tokens', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade_users() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_tokens_user_id'), table_name='user_tokens')
    op.drop_table('user_tokens')
    op.drop_index(op.f('ix_user_passwords_user_id'), table_name='user_passwords')
    op.drop_table('user_passwords')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###

