import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'front-end';
  games;

  async ngOnInit() {
  	let response = await fetch('https://stacksbystacks.com/Sql.php');
  	this.games = await response.json();
  }
}
