"""
VideoAnalysis model - stores video analysis results
"""
import uuid
from datetime import datetime
from . import db


class VideoAnalysis(db.Model):
    """
    VideoAnalysis model - represents a video analysis result
    """
    __tablename__ = 'video_analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = db.Column(db.String(200), nullable=False, unique=True)  # Unique file identifier from GenAI
    analysis_content = db.Column(db.Text, nullable=True)  # Markdown content
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'file_id': self.file_id,
            'analysis_content': self.analysis_content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<VideoAnalysis {self.id}: {self.file_id}>'
    
    @classmethod
    def get_by_file_id(cls, file_id):
        """Get video analysis by file_id"""
        return cls.query.filter_by(file_id=file_id).first()
    
    @classmethod
    def create_or_update(cls, file_id, analysis_content):
        """Create or update video analysis by file_id"""
        video_analysis = cls.get_by_file_id(file_id)
        if video_analysis:
            video_analysis.analysis_content = analysis_content
        else:
            video_analysis = cls(
                file_id=file_id,
                analysis_content=analysis_content
            )
            db.session.add(video_analysis)
        db.session.commit()
        return video_analysis
