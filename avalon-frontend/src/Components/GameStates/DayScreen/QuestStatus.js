import React from 'react';

import AppContext from '../../../AppContext';

class QuestStatus extends React.Component {
  render() {
    const {quests} = this.context;

    let indicatorsDOM = [];

    quests.forEach((quest, index) => {
      if (quest) {
        indicatorsDOM.push(
          <div class="uk-icon-button uk-button-primary"></div>
        );
      } else if (quest === false) {
        indicatorsDOM.push(
          <div class="uk-icon-button uk-button-danger"></div>
        )
      } else {
        indicatorsDOM.push(
          <div class="uk-icon-button"></div>
        )
      }
    })

    return (
      <div>{indicatorsDOM}</div>
    );
  }
}

QuestStatus.contextType = AppContext;

export default QuestStatus;
