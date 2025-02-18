import React from 'react';

import AppContext from '../../../AppContext';

class OnQuest extends React.Component {
  state = {
    voted: false
  }

  onSucceedQuest = (e) => {
    e.preventDefault();

    const {socketMaster} = this.context;

    socketMaster.emit('perform_quest', {vote: true});
    this.setState({voted: true});
  }

  onFailQuest = (e) => {
    e.preventDefault();

    const {socketMaster} = this.context;

    socketMaster.emit('perform_quest', {vote: false});
    this.setState({voted: true});
  }

  render() {
    const {voted} = this.state;
    const {role} = this.context;

    const isMinion = (role === 'minion');
    let btnFail = undefined;

    if (isMinion) {
      btnFail = (
        <button
          className="uk-button uk-button-danger uk-width-1-1 uk-margin-small-bottom"
          onClick={this.onFailQuest}
          disabled={voted}
        >
          Fail Quest
        </button>
      );
    }

    return (
      <div className="uk-container uk-margin-top">
        <h3 className="uk-heading-line uk-text-center"><span>Quest Time</span></h3>
        <p>You are on the quest. Choose your poison!</p>
        <button
          className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
          onClick={this.onSucceedQuest}
          disabled={voted}
        >
          Succeed Quest
        </button>
        {btnFail}
      </div>
    );
  }
}

OnQuest.contextType = AppContext;

export default OnQuest;