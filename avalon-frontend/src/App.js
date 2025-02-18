import React from 'react';
import { ToastContainer, toast } from 'react-toastify';
import io from 'socket.io-client';

import Lobby from './Components/Lobby';
import Login from './Components/Login';
import Setup from './Components/Setup';
import ReadyScreen from './Components/ReadyScreen';

import DayScreen from './Components/GameStates/DayScreen';
import ApproveTeam from './Components/GameStates/ApproveTeam';
import QuestScreen from './Components/GameStates/QuestScreen';
import EndScreen from './Components/GameStates/EndScreen';

import AppContext from './AppContext';

class App extends React.Component {
  state = {
    message: '',

    state: 'lobby',
    role: '',
    my_name: '',

    uuid: '',
    players: [],
    players_accepted: [],
    picked_players: [],
    host: '',
    team_leader: '',
    quests: [null, null, null, null, null],
    failed: -1,
    players_yes: undefined,
    players_no: undefined,

    team_vote_history: {},

    roles: {},
    humans_victory: null,

    socketMaster: undefined
  };

  componentDidMount = () => {
    const toastProps = {
      position: "top-center",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    };
    const socketMaster = io('http://localhost:5000');

    socketMaster.on('welcome', (data) => {
      this.setState({message: data.message});
    });

    socketMaster.on('create_room_listener', (data) => {
      this.setState({...data});
    });

    socketMaster.on('room_listener', (data) => {
      this.setState({...data});
    });

    socketMaster.on('game_listener', (data) => {
      if (data.hasOwnProperty('day')) {
        // If the data has a day property, save the team voting data to the history
        const day = parseInt(data.day) + 1;
        const dayKey = 'Day ' + day.toString();

        let {team_vote_history} = this.state;

        if (team_vote_history.hasOwnProperty(dayKey)) {
          team_vote_history[dayKey].push(
            {
              picked_players: this.state.picked_players,
              players_yes: data.players_yes,
              players_no: data.players_no
            }
          );
        } else {
          team_vote_history = {...team_vote_history, [dayKey]: [
            {
              picked_players: this.state.picked_players,
              players_yes: data.players_yes,
              players_no: data.players_no
            }
          ]}
        }

        this.setState({team_vote_history});
      }

      this.setState({...data});
    });

    socketMaster.on('sys_message', (data) => {
      if ('error' in data) {
        toast.error(data.error, toastProps);
      } else if ('message' in data) {
        toast.success(data.message, toastProps);
      }
    })

    this.setState({socketMaster});
  }

  render() {
    const {state, uuid} = this.state;

    let displayDOM = undefined;

    if (state === 'lobby') {
      if (uuid) {
        displayDOM = <Lobby />;
      } else {
        displayDOM = <Login />;
      }
    } else if (state === 'game_state_setup') {
      displayDOM = <Setup />;
    } else if (state === 'game_state_begin') {
      displayDOM = <ReadyScreen />;
    } else if (state === 'game_state_day') {
      displayDOM = <DayScreen />;
    } else if (state === 'game_state_vote_team') {
      displayDOM = <ApproveTeam />;
    } else if (state === 'game_state_quest') {
      displayDOM = <QuestScreen />;
    } else if (state === 'game_state_finished') {
      displayDOM = <EndScreen />;
    }

    return (
      <React.Fragment>
        <AppContext.Provider value={this.state}>
          {displayDOM}
        </AppContext.Provider>
        <ToastContainer />
      </React.Fragment>
    );
  }
}

export default App;
