import React from 'react';

import OnQuest from './OnQuest';
import NonQuest from './NonQuest';

import AppContext from '../../../AppContext';

class QuestScreen extends React.Component {
  render() {
    const {my_name, picked_players} = this.context;

    const isOnQuest = (picked_players.indexOf(my_name) >= 0 ? true : false);

    let displayDOM = <NonQuest />;

    if (isOnQuest) {
      displayDOM = <OnQuest />;
    }

    return displayDOM;
  }
}

QuestScreen.contextType = AppContext

export default QuestScreen;