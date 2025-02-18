import React from 'react';

import AppContext from '../../../AppContext';

class EndScreen extends React.Component {
  render() {
    const {humans_victory, roles} = this.context;

    let whoWonDOM = undefined;

    if (humans_victory) {
      whoWonDOM = <h3 className="uk-heading-line uk-text-center"><span>Humans Won</span></h3>;
    } else {
      whoWonDOM = <h3 className="uk-heading-line uk-text-center"><span>Minions Won</span></h3>;
    }

    let roleListDOM = [];

    for (const player in roles) {
      const role = roles[player];

      roleListDOM.push(
        <div key={player} className="uk-flex uk-margin">
          <div className="uk-flex-1">
            {player}
            {
              role === 'servant' ?
                <span className="uk-label uk-margin-small-left">{role}</span> :
                <span className="uk-label uk-label-danger uk-margin-small-left">{role}</span>
            }
          </div>
        </div>
      );
    }

    return (
      <div className="uk-container uk-margin-top">
        {whoWonDOM}
        {roleListDOM}
      </div>
    );
  }
}

EndScreen.contextType = AppContext;

export default EndScreen;
