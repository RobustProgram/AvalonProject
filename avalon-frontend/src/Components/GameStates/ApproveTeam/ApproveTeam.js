import React from 'react';

import AppContext from '../../../AppContext';

class ApproveTeam extends React.Component {
  state = {
    voted: false
  }

  onApprove = (e) => {
    e.preventDefault();

    const {socketMaster} = this.context;

    socketMaster.emit('vote_team', {vote: true});
    this.setState({voted: true});
  }

  onDisapprove = (e) => {
    e.preventDefault();

    const {socketMaster} = this.context;

    socketMaster.emit('vote_team', {vote: false});
    this.setState({voted: true});
  }

  render() {
    const {voted} = this.state;
    const {picked_players} = this.context;

    let pickedPlayerDOM = [];

    picked_players.forEach((player, index) => {
      pickedPlayerDOM.push(
        <div key={player} className="uk-flex uk-margin">
          <div className="uk-flex-1">
            {index}: {player}
          </div>
        </div>
      );
    });

    return (
      <div className="uk-container uk-margin-top">
        <h3 className="uk-heading-line uk-text-center"><span>Vote For Team</span></h3>
        {pickedPlayerDOM}
        <button
          className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
          onClick={this.onApprove}
          disabled={voted}
        >
          Approve Team
        </button>
        <button
          className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
          onClick={this.onDisapprove}
          disabled={voted}
        >
          Disapprove Team
        </button>
      </div>
    );
  }
}

ApproveTeam.contextType = AppContext;

export default ApproveTeam;
