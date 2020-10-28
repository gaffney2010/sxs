import { Component, OnInit } from '@angular/core';
import { GameDate } from './shared_interfaces';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title: string = 'front-end';
  dates: Array<GameDate>

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'game_date');
    url.searchParams.append('table', 'game');
    url.searchParams.append('order', 'game_date desc');
  	let response = await fetch(url.href);
  	this.dates = await response.json();
  }
}
