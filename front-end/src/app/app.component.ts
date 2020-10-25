import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'front-end';
  dates;

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'game_date');
    url.searchParams.append('table', 'game');
    url.searchParams.append('order', 'game_date desc');
  	let response = await fetch(url.href);
  	this.dates = await response.json();
  }
}
