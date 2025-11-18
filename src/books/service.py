from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import Book
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(Book.created_at.desc())
       
        results = await session.execute(statement)
        
        return results.scalars().all()
    
    async def get_book(self,book_uid:str, session: AsyncSession):
        try:
            statement = select(Book).where(Book.uid == book_uid)
            results = await session.execute(statement)
            book = results.scalars().one_or_none()
            return book if book is not None else None
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_book: {e}")
            await session.rollback()
            raise

    async def create_book(self,book_data: BookCreateModel, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        
        # Convert the published_date string to date object
        published_date_str = book_data_dict.pop("published_date")
        published_date_obj = datetime.strptime(published_date_str, "%Y-%m-%d").date()
        
        new_book = Book(
            **book_data_dict,
            published_date=published_date_obj
        )
        
        session.add(new_book)
        
        await session.commit()
        
        return new_book

    async def update_book(self,book_uid:str, update_data: BookUpdateModel, session: AsyncSession):
        try:
            book_to_update = await self.get_book(
                book_uid, 
                session
            )
            if not book_to_update:
                return None
            else:
                update_data_dict = update_data.model_dump()
                
                for key, value in update_data_dict.items():
                    setattr(book_to_update, key, value)
                    
                await session.commit()
                
                return book_to_update
        except SQLAlchemyError as e:
            logger.error(f"Database error in update_book: {e}")
            await session.rollback()
            raise
    
    async def delete_book(self,book_uid:str, session: AsyncSession):
        book_to_delete = await self.get_book(
            book_uid, 
            session
        )
        
        if not book_to_delete:
            return None
        else:
            session.delete(book_to_delete)  # Remove await - delete is not async
            
            await session.commit()
            
            return {"message": "Book deleted successfully"}