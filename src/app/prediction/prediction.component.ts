import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.css']
})
export class PredictionComponent implements OnInit {
  form: any = {
    place:'',
    season:'',
    cropName:'',
    areaPlanted:'',
    totalRainfall:'',
    maxTemp:'',
    soilType:'',
    soilPh:'',
    algorithm:''
  }
  constructor() { }

  success = false;
  totalProduction = 0;

  ngOnInit(): void {
  }

  onSubmit(){
    console.log(this.form);

    // this.totalProduction = Math.round(Math.random() * 1000);
  }

}
