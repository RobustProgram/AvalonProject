import React from 'react';

class DeselectPlayer extends React.Component {
  deselectPlayer = (e) => {
    e.preventDefault();
    this.props.deselectPlayer(this.props.playerName);
  }

  render() {
    return (
      <button
        className="uk-icon-button uk-button-danger"
        data-uk-tooltip="Deselect the user"
        data-uk-icon="close"
        onClick={this.deselectPlayer}
      ></button>
    );
  }
}

export default DeselectPlayer;
