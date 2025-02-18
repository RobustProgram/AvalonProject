import ReadyScreen from './ReadyScreen';
import AppContext from '../../AppContext';

const MockedReadyScreen = () => {
  return (
    <AppContext.Provider value={{players: ['player1', 'player2', 'player3'], players_accepted: ['player1', 'player2'], role: 'Minion'}}>
      <ReadyScreen />
    </AppContext.Provider>
  )
}

export default {
  title: 'Pages/ReadyScreen',
  component: MockedReadyScreen,
};

export const ReadyScreenPage = {};