import React from 'react';

class KickPlayer extends React.Component {
  kickPlayer = (e) => {
    e.preventDefault();
    this.props.kickPlayer(this.props.playerName);
  }

  render() {
    return (
      <button
        className="uk-icon-button uk-button-danger"
        data-uk-tooltip="Kick the user"
        data-uk-icon="close"
        onClick={this.kickPlayer}
      ></button>
    );
  }
}

export default KickPlayer;
