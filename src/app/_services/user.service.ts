import { RegUser } from './../models/regUser.model';
import { User } from './../models/user.model';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from "src/environments/environment";

const API_URL = environment.BaseUrl;

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) { }

  getPublicContent(): Observable<any> {
    return this.http.get(API_URL + 'all', { responseType: 'text' });
  }

  getUserBoard(): Observable<any> {
    return this.http.get(API_URL + 'user', { responseType: 'text' });
  }

  getModeratorBoard(): Observable<any> {
    return this.http.get(API_URL + 'mod', { responseType: 'text' });
  }

  getAdminBoard(): Observable<any> {
    return this.http.get(API_URL + 'admin', { responseType: 'text' });
  }

  getAllUsers():Observable<any> {
    return this.http.get(API_URL + 'users', { responseType: 'json' });
  }

  changeAccountStatus(user: User):Observable<any> {
    return this.http.put(API_URL + 'user', user);
  }

  createUser(user: RegUser):Observable<any> {
    return this.http.post(API_URL + 'user', user);
  }

}
