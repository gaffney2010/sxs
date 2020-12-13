import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ExpertDetails } from '../shared_interfaces';

@Component({
  selector: 'app-expert-id',
  templateUrl: './expert-id.component.html',
  styleUrls: ['./expert-id.component.css']
})
export class ExpertIdComponent implements OnInit {
  stacks: Array<ExpertDetails>;
  expert_name: string;
  expert_id: number;

  constructor(private route: ActivatedRoute) { }

  isAwayWon(stack: ExpertDetails) {
    return stack.home_score > stack.away_score;
  }

  isHomeWon(stack: ExpertDetails) {
    return stack.home_score < stack.away_score;
  }

  spread(stack: ExpertDetails) {
    let result = "";
    if (stack.spread_favorite == stack.predicted_winner_id_with_spread) {
      result += "-";
    } else {
      result += "+";
    }
    result += stack.spread_amt;
    return result;
  }

  async ngOnInit() {
    this.expert_id = +this.route.snapshot.paramMap.get('expert_id');

    var url = new URL('https://stacksbystacks.com/Sql.php');
    url.searchParams.append('columns', 'expert_text');
    url.searchParams.append('table', 'expert');
    url.searchParams.append('where', 'expert_id=' + this.expert_id);
  	let response = await fetch(url.href);
  	let json_arr = await response.json();
  	this.expert_name = json_arr[0].expert_text;

    var url2 = new URL('https://stacksbystacks.com/Sql.php');
    url2.searchParams.append('columns', 'expert_id,game_date,home_team_name,away_team_name,home_score,away_score,spread_favorite,spread_amt,link,predicted_winner_id_with_spread,predicted_winner_name');
    url2.searchParams.append('table', 'expert_details');
    url2.searchParams.append('where', 'expert_id=' + this.expert_id);
    url2.searchParams.append('order', 'game_date desc');
  	let response2 = await fetch(url2.href);
  	this.stacks = await response2.json();
  }

}
