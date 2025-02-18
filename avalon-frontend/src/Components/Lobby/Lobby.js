import React from 'react';
import KickPlayer from './KickPlayer';

import AppContext from '../../AppContext';

class Lobby extends React.Component {
  kickPlayer = (playerName) => {
    const {socketMaster} = this.context;

    socketMaster.emit('kick_player', {'name': playerName});
  }

  leaveRoom = (e) => {
    const {socketMaster} = this.context;
    
    e.preventDefault();
    socketMaster.emit('leave_room');
  }

  startGame = (e) => {
    const {socketMaster} = this.context;

    e.preventDefault();
    socketMaster.emit('start_setup');
  }

  render() {
    const {uuid, players, host} = this.context;

    let playersElms = [];
    players.map((player, index) => {
      playersElms.push(
        <div key={player} className="uk-flex uk-margin">
          <div className="uk-flex-1">
            {index}: {player}
            {
              player === host ?
                <span className="uk-label uk-label-warning uk-margin-small-left">
                  HOST
                </span> :
                undefined
            }
          </div>
          <div>
            {
              player !== host ?
                <KickPlayer kickPlayer={this.kickPlayer} playerName={player}/> :
                undefined
            }
          </div>
        </div>
      );
    });

    return (
      <div className="uk-container uk-margin-top">
        <div className="uk-margin">
          <label className="uk-form-label">
            Room ID (Send this to your friends to join the room)
          </label>
          <div className="uk-form-controls">
            <input
              className="uk-input"
              type="text"
              value={uuid}
              disabled
            />
          </div>
        </div>
        <h3 className="uk-heading-line uk-text-center"><span>Players</span></h3>
        {playersElms}
        <button
          className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
          onClick={this.startGame}
        >
          Start Game
        </button>
        <button
          className="uk-button uk-button-danger uk-width-1-1 uk-margin-small-bottom"
          onClick={this.leaveRoom}
        >
          Leave Room
        </button>
      </div>
    );
  }
}

Lobby.contextType = AppContext;

export default Lobby;
