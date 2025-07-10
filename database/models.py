from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from database.config import Base



class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    activated = Column(Boolean, nullable=False, default=False)

    switchboards = relationship("Switchboard", back_populates="project")
    audioboards = relationship("Audioboard", back_populates="project")
    dht_sensors = relationship('DHT_sensor', back_populates="project")
    servoboards = relationship("Servoboard", back_populates="project")

    def __repr__(self):
        return f'<Project(id={self.id}, name={self.name}, description={self.description}, activated={self.activated})>'



class Switchboard(Base):
    __tablename__ = 'switchboards'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(46), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete="SET NULL"))

    project = relationship(Project, back_populates='switchboards')
    switchs = relationship('Switch', back_populates='switchboard')

    def __repr__(self):
        return f'<Switchboard(id={self.id}, name={self.name}, ip_address={self.ip_address}, chip_id={self.chip_id}, project_id={self.project_id})>'



class Switch(Base):
    __tablename__ = 'switchs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    position = Column(Integer, nullable=False)
    state = Column(Boolean, nullable=False, default=False)
    locked = Column(Boolean, nullable=False, default=False)
    switchboard_id = Column(String(255), ForeignKey('switchboards.id', ondelete="CASCADE"))

    switchboard = relationship('Switchboard', back_populates='switchs')

    def __repr__(self):
        return f'<Switch(id={self.id}, name={self.name}, position={self.position}, state={self.state}, switchboard_id={self.switchboard_id})>'



class Audioboard(Base):
    __tablename__ = "audioboards"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(46), nullable=False)
    api_port = Column(Integer, nullable=False, default=80)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete="SET NULL"))

    project = relationship(Project, back_populates="audioboards")
    audiotracks = relationship("Audiotrack", back_populates="audioboard")

    def __repr__(self):
        return f'<Audioboard(id={self.id}, name={self.name}, ip_address={self.ip_address}, api_port={self.api_port}, project_id={self.project_id})>'


class Audiotrack(Base):
    __tablename__ = 'audiotracks'

    track_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    audio_path = Column(String(999), nullable=False)
    loop = Column(Boolean, nullable=False, default=False)
    random = Column(Boolean, nullable=False, default=False)
    audioboard_id = Column(String(255), ForeignKey('audioboards.id', ondelete="CASCADE", onupdate="CASCADE"))

    audioboard = relationship('Audioboard', back_populates="audiotracks")

    __table_args__ = (
        UniqueConstraint('name', 'audioboard_id', name='unique_audiotrack_per_audioboard'),
    )

    def __repr__(self):
        return f'<Audiotrack(id={self.track_id}, name={self.name}, audio_path={self.audio_path}, loop={self.loop}, random={self.random}, audioboard_id={self.audioboard_id})>'



class Servoboard(Base):
    __tablename__ = 'servoboards'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(46), nullable=False)
    current_animation = Column(String(255), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete="SET NULL"))

    project = relationship(Project, back_populates='servoboards')

    def __repr__(self):
        return f'<Servoboard(id={self.id}, ip_address={self.ip_address}, project_id={self.project_id})>'


class DHT_sensor(Base):
    __tablename__ = "dht_sensors"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(46), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete="SET NULL"))

    project = relationship(Project, back_populates="dht_sensors")

    def __repr__(self):
        return f'<DHT_sensor(id={self.id}, name={self.name}, ip_address={self.ip_address}, project_id={self.project_id})>'