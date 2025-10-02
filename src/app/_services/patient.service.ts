import { Patient } from './../models/patient.model';
import { User } from './../models/user.model';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from "src/environments/environment";
import { PatientRecord } from '../models/record.model';

const API_URL = environment.BaseUrl;

@Injectable({
  providedIn: 'root'
})

export class PatientService {

  constructor(private http: HttpClient) { }

  createPatient(patient: Patient): Observable<any> {
    return this.http.post(API_URL + 'patient', patient);
  }

  createRecord(record: PatientRecord): Observable<any> {
    return this.http.post(API_URL + 'record', record);
  }

}
