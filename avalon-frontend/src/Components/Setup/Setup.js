import React from 'react';

import AppContext from '../../AppContext';

class Setup extends React.Component {
  onStartGame = (e) => {
    e.preventDefault();

    const {socketMaster} = this.context;

    socketMaster.emit('start_game', {});
  }

  render() {
    return (
      <div className="uk-container uk-margin-top">
        <p className="uk-text-large">Under Development</p>
        <p>
          This version of the game does not include special characters. They will be added later.
        </p>
        <button
          className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
          onClick={this.onStartGame}
        >
          Finish Setup
        </button>
      </div>
    );
  }
}

Setup.contextType = AppContext;

export default Setup;
