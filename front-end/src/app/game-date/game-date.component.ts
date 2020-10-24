import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-game-date',
  templateUrl: './game-date.component.html',
  styleUrls: ['./game-date.component.css']
})
export class GameDateComponent implements OnInit {
  @Input() game_date;
  games;

  constructor() { }

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'home_score,away_score');
    url.searchParams.append('table', 'game');
    url.searchParams.append('where', 'game_date=' + this.game_date);
  	let response = await fetch(url.href);
  	this.games = await response.json();
  }

}
