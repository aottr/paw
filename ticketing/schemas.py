from ninja import ModelSchema
from ninja.orm import create_schema
from .models import Ticket, Category, Comment, FileAttachment
from core.models import PawUser

class UserSchema(ModelSchema):
    class Meta:
        model = PawUser
        fields = ['id', 'username', 'profile_picture']

class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = ['id', 'name']
        
class FileAttachmentSchema(ModelSchema):
    class Meta:
        model = FileAttachment
        fields = ['id', 'file', 'uploaded_at']

class TicketSchema(ModelSchema):
    """Schema for ticket with nested user information."""
    user: UserSchema
    assigned_to: UserSchema | None = None
    category: CategorySchema | None = None
    
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'user', 'assigned_to', 'category', 'status', 'priority', 'created_at', 'updated_at']
        
class TicketDetailSchema(ModelSchema):
    user: UserSchema
    assigned_to: UserSchema | None = None
    category: CategorySchema | None = None
    follow_up_to: TicketSchema | None = None
    followed_up_by: list[TicketSchema] = []
    attachments: list[FileAttachmentSchema] = []
    
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'user', 'assigned_to', 'category', 'status', 'priority', 'created_at', 'updated_at', 'description', 'follow_up_to']

    @staticmethod
    def resolve_attachments(obj: Ticket):
        """Resolve attachments from reverse ForeignKey relationship."""
        return obj.fileattachment_set.all()
        
class CommentSchema(ModelSchema):
    user: UserSchema
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']