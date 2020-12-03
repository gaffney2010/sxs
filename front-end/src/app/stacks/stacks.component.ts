import { Component, OnInit } from '@angular/core';
import { Game } from '../shared_interfaces';

class SeasonWeek {
  season: number;
  week: number;

  constructor(season: number, week: number) {
    this.season = season;
    this.week = week;
  }
}

@Component({
  selector: 'app-stacks',
  templateUrl: './stacks.component.html',
  styleUrls: ['./stacks.component.css']
})
export class StacksComponent implements OnInit {
  games: Array<Game>;
  _week: SeasonWeek;
  page: number;

  async updatePage() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'game_date,home_team_id,home_score,away_score,home_team_name,away_team_name,play_status');
    url.searchParams.append('table', 'games_with_team_names');
    url.searchParams.append('where', 'season=' + this._week.season + " and week=" + this._week.week);
    url.searchParams.append('order', 'game_date desc');
  	let response = await fetch(url.href);
  	this.games = await response.json();
  }

  set week(value: SeasonWeek) {
    this._week = value;
    this.updatePage();
  }

  get week(): SeasonWeek {
    return this._week;
  }

  nextPage() {
    let current_week = this.week.week;
    let current_season = this.week.season;

    if (this.week.week > 1) {
      this.week = new SeasonWeek(current_season, current_week-1);
    } else {
      this.week = new SeasonWeek(current_season-1, 16);
    }

    this.page += 1;
  }

  previousPage() {
    let current_week = this.week.week;
    let current_season = this.week.season;

    if (this.week.week == 16) {
      this.week = new SeasonWeek(current_season+1, 1);
    } else {
      this.week = new SeasonWeek(current_season, current_week+1);
    }

    this.page -= 1;
  }

  constructor() { }

  async ngOnInit() {
    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'season,week');
    url.searchParams.append('table', 'game');
    url.searchParams.append('order', 'game_date desc');
    url.searchParams.append('limit', '1');
  	let response = await fetch(url.href);
  	let week_array: Array<SeasonWeek> = await response.json();
  	this.week = week_array[0];
  	this.page = 0;
  }
}
