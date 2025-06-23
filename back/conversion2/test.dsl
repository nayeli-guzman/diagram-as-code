<<<<<<< HEAD

    Table users {
      id int [pk]
      name varchar
    }
    
=======
Table users {
  id integer [pk]
  name varchar
  email varchar
}

Table posts {
  id integer [pk]
  user_id integer [ref: > users.id]
  title varchar
}
>>>>>>> 3f161eb (..)
