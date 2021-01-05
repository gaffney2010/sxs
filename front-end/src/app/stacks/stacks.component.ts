import { Component, OnInit } from '@angular/core';
import { Game } from '../shared_interfaces';

@Component({
  selector: 'app-stacks',
  templateUrl: './stacks.component.html',
  styleUrls: ['./stacks.component.css']
})
export class StacksComponent implements OnInit {
  games: Array<Game>;
  page: number;

  async updatePage() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'game_key,game_date,home_score,away_score,home_team_name,away_team_name,play_status');
    url.searchParams.append('table', 'games_with_team_names');
    url.searchParams.append('where', 'game_date>20200914')
    url.searchParams.append('order', 'game_date desc');
  	let response = await fetch(url.href);
  	this.games = await response.json();
  }

  nextPage() {
    // Currently does nothing.

    this.page += 1;
  }

  previousPage() {

    this.page -= 1;
  }

  constructor() { }

  async ngOnInit() {
  	this.page = 0;
  	this.updatePage();
  }
}
