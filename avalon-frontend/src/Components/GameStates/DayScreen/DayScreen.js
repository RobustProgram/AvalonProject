import React from 'react';

import SelectPlayer from './SelectPlayer';
import DeselectPlayer from './DeselectPlayer';
import QuestStatus from './QuestStatus';

import AppContext from '../../../AppContext';

class DayScreen extends React.Component {
  confirmTeam = () => {
    const {socketMaster} = this.context;

    socketMaster.emit('confirm_team');
  }

  selectPlayer = (playerName) => {
    const {socketMaster} = this.context;

    socketMaster.emit('pick_player', {'player': playerName});
  }

  deselectPlayer = (playerName) => {
    const {socketMaster} = this.context;

    socketMaster.emit('unpick_player', {'player': playerName});
  }

  render() {
    const {my_name, players, picked_players, team_leader, team_vote_history} = this.context;
    const isThisPlayerLeader = (my_name === team_leader);

    let playersDOM = [];

    players.map((player, index) => {
      const isPlayerPicked = (picked_players.indexOf(player) >= 0 ? true : false);
      const isPlayerLeader = (player === team_leader);

      playersDOM.push(
        <div key={player} className="uk-flex uk-margin">
          <div className="uk-flex-1">
            {index}: {player}
            {
              isPlayerLeader ?
                <span className="uk-label uk-label-warning uk-margin-small-left">
                  Team Leader
                </span> : undefined
            }
            {
              isPlayerPicked ?
              <span className="uk-label uk-label-success uk-margin-small-left">
                Chosen for quest
              </span> : undefined
            }
          </div>
          {
            isThisPlayerLeader ?
            <div>
              {
                isPlayerPicked ?
                  <DeselectPlayer playerName={player} deselectPlayer={this.deselectPlayer} /> :
                  <SelectPlayer playerName={player} selectPlayer={this.selectPlayer} />
              }
            </div> : undefined
          }
        </div>
      );
    });

    let historyDOM = [];

    for (const day in team_vote_history) {
      let voteDOM = [];

      for (const dayData of team_vote_history[day]) {
        let playerListDOM = [];

        for (const player of dayData.players_yes) {
          playerListDOM.push(
            <div key={player} className="uk-margin">
              {player} <span className="uk-label uk-label-success uk-margin-small-left">Yes</span>
            </div>
          )
        }

        for (const player of dayData.players_no) {
          playerListDOM.push(
            <div key={player} className="uk-margin">
              {player} <span className="uk-label uk-label-danger uk-margin-small-left">No</span>
            </div>
          )
        }

        let pickedPlayerListDOM = [];

        for (const player of dayData.picked_players) {
          pickedPlayerListDOM.push(
            <div key={player} className="uk-margin">
              {player}
            </div>
          )
        }

        voteDOM.push(
          <React.Fragment>
            <h5>Players</h5>
            {pickedPlayerListDOM}
            <h5>Votes</h5>
            {playerListDOM}
            <hr className="uk-divider-icon"></hr>
          </React.Fragment>
        );
      }

      historyDOM.push(
        <li>
          <a class="uk-accordion-title" href="#">{day}</a>
          <div class="uk-accordion-content">
            {voteDOM}
          </div>
        </li>
      );
    }

    return (
      <div className="uk-container uk-margin-top">
        <button
          className="uk-button uk-button-default uk-margin-bottom	"
          type="button"
          data-uk-toggle="target: #offcanvas-usage"
        >
          Check History
        </button>
        <QuestStatus />
        <h3 className="uk-heading-line uk-text-center"><span>Day Time</span></h3>
        {playersDOM}
        {
          isThisPlayerLeader ?
            <button
              className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
              onClick={this.confirmTeam}
            >
              Chose Team
            </button> : undefined
        }
        <div id="offcanvas-usage" data-uk-offcanvas>
          <div class="uk-offcanvas-bar">
              <button class="uk-offcanvas-close" type="button" data-uk-close></button>
              <ul data-uk-accordion>{historyDOM}</ul>
          </div>
        </div>
      </div>
    );
  }
}

DayScreen.contextType = AppContext;

export default DayScreen;
