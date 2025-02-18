import React from 'react';

import AppContext from '../../AppContext';

class ReadyScreen extends React.Component {
  onReady = e => {
    e.preventDefault();

    const {socketMaster} = this.context;

    socketMaster.emit('accept_role');
  }

  render() {
    const {players, players_accepted, role} = this.context;

    let playersDOM = [];

    players.map((player, index) => {
      const didPlayerAccept = (players_accepted.indexOf(player) >= 0 ? true : false);

      playersDOM.push(
        <div key={player} className="uk-flex uk-margin">
          <div className="uk-flex-1">
            {index}: {player}
            {
              didPlayerAccept ?
                <span className="uk-label uk-label-success uk-margin-small-left">
                  Ready
                </span> :
                <span className="uk-label uk-label-danger uk-margin-small-left">
                  Not Ready
                </span>
            }
          </div>
        </div>
      );
    });

    return (
      <div className="uk-container uk-margin-top">
        <h3 className="uk-heading-line uk-text-center"><span>Your Role</span></h3>
        <p>You are {role}</p>
        <h3 className="uk-heading-line uk-text-center"><span>Players</span></h3>
        {playersDOM}
        <button
          className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
          onClick={this.onReady}
        >
          Ready
        </button>
      </div>
    );
  }
}

ReadyScreen.contextType = AppContext;

export default ReadyScreen;
