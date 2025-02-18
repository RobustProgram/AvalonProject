import React from 'react';
import AppContext from '../../AppContext';

export default function Setup() {
  const { socketMaster } = React.useContext(AppContext);

  function onStartGame() {
    socketMaster.emit('start_game', {});
  }

  return (
    <div className="uk-container uk-margin-top">
      <p className="uk-text-large">Under Development</p>
      <p>
        This version of the game does not include special characters. They will be added later.
      </p>
      <button
        className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
        onClick={onStartGame}
      >
        Finish Setup
      </button>
    </div>
  );
};
