from fastapi import APIRouter,status,HTTPException,Depends
from models.todo import Todo
from pydantic import BaseModel
from database import Base, engine,SessionLocal
from sqlalchemy.orm import Session


router=APIRouter(prefix='/app/v1',tags=['Todos'])

class TodoCreate(BaseModel):
    title:str
    description:str
    completed:bool=False

class TodoInDB(BaseModel):
        id:int
        title:str
        description:str
        completed:bool
        class Config:
            from_attributes=True

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

#API for creating a new TODOs
@router.post('/createtodos',status_code=status.HTTP_201_CREATED)
def create_todo(item:TodoCreate,user_id: int,db:Session=Depends(get_db)):
    # Let database auto-generate ID (assuming id=Column(Integer, primary_key=True))
    todo = Todo(
        title=item.title,
        description=item.description,
        completed=item.completed,
        user_id=user_id  # attach logged-in user
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)  # Gets the auto-generated ID
    return {'message': 'TODO created successfully', 'todo': todo}

#API for getting all TODOs
# @router.get('/getalltodos',status_code=status.HTTP_200_OK)
# def get_all_todos(db:Session=Depends(get_db)):
#     todos=db.query(Todo).all()
#     return todos

@router.get("/getalltodos/{user_id}")
def get_user_todos(user_id: int, db: Session = Depends(get_db)):
    todos = db.query(Todo).filter(Todo.user_id == user_id).all()
    return todos


#API for getting a Todo by id
@router.get('/gettodosbyid/{item_id}',status_code=status.HTTP_200_OK)
def get_todo_by_id(item_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')    
    return todo

#API for deleting a Todo by id
@router.delete('/deletetodosbyid/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_by_id(item_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')
    db.delete(todo)
    db.commit()
    return {'message':f'TODO with id {item_id} deleted successfully'}
    
#API for updating a Todo by id
@router.put('/updatetodosbyid/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
def update_todo_by_id(item_id:int,data:TodoCreate,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')
    
    todo.title=data.title
    todo.description=data.description
    todo.completed=data.completed
    db.commit()
    return {'message':f'TODO with id {item_id} updated successfully'}
    
#API for toggling the completed status of a Todo by id
@router.patch('/toggletodosbyid/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
def toggle_todo_by_id(item_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')
    todo.completed=not todo.completed
    db.commit()
    return {'message':f'TODO with id {item_id} toggled successfully'}
    

# #API for deleting all TODOs
# @router.delete('/deletealltodos',status_code=status.HTTP_204_NO_CONTENT)
# def delete_all_todos(db:Session=Depends(get_db)):
#     todos=db.query(Todo).all()
#     if len(todos)==0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No TODOs found')
#     db.query(Todo).delete(synchronize_session=False)
#     db.commit()
#     return {'message':'All TODOs deleted successfully'}

# #API for deleting all TODOs
@router.delete('/deletealltodos/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_all_todos_for_user(user_id: int, db: Session = Depends(get_db)):
    todos = db.query(Todo).filter(Todo.user_id == user_id).all()
    if not todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No TODOs found for user with id {user_id}'
        )
    db.query(Todo).filter(Todo.user_id == user_id).delete(synchronize_session=False)
    db.commit()
    return {'message': f'All TODOs for user {user_id} deleted successfully'}

#Api to get user specific TODOs
@router.get('/getusertodos/{user_id}',status_code=status.HTTP_200_OK )
def get_user_todos(user_id:int,db:Session=Depends(get_db)):
    todos=db.query(Todo).filter(Todo.user_id==user_id).all()
    if len(todos)==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No TODOs found for user with id {user_id}')
    return todos