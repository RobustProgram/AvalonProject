import React from 'react';

class SelectPlayer extends React.Component {
  selectPlayer = (e) => {
    e.preventDefault();
    this.props.selectPlayer(this.props.playerName);
  }

  render() {
    return (
      <button
        className="uk-icon-button uk-button-primary"
        data-uk-tooltip="Select the user"
        data-uk-icon="check"
        onClick={this.selectPlayer}
      ></button>
    );
  }
}

export default SelectPlayer;
