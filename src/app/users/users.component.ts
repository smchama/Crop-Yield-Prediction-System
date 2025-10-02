import { RegUser } from './../models/regUser.model';
import { User } from './../models/user.model';
import { UserService } from './../_services/user.service';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent implements OnInit {
  form: RegUser = {
    id:0,
    firstname: '',
    lastname:'',
    email:'',
    username: '',
    password:'',
    active:0,
    created:''
  };
  success = false;
  users: User[] = [];

  constructor(private userService: UserService) { }

  ngOnInit(): void {
    this.loadAllUsers();

    setTimeout(()=>{
      this.success = false;
    }, 2000);

  }

  loadAllUsers(){
    this.userService.getAllUsers().subscribe((user:User[]) =>{
        this.users = user;
        console.log(this.users);
    });
  }

  setActive(user:User){
    user.active = user.active ? 0 : 1;
    this.userService.changeAccountStatus(user).subscribe(data =>{
      console.log(data);
    })
  }

  onSubmit(){
    this.loadAllUsers();
    this.userService.createUser(this.form).subscribe(data =>{
      this.success = true
      setTimeout(()=>{
        this.success = false;
      }, 2000);
    })
  }

}
