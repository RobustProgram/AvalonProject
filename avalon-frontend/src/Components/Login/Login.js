import React from 'react';

import AppContext from '../../AppContext';

class Login extends React.Component {
  constructor(props) {
    super(props);

    this.roomNameRef = React.createRef();
    this.userNameRef = React.createRef();

    this.state = {
      roomNameLen: 0
    };
  }

  onJoinCreateRoom = (e) => {
    e.preventDefault();

    const { socketMaster } = this.context;

    const roomName = this.roomNameRef.current.value;
    const userName = this.userNameRef.current.value;

    if (roomName) {
      socketMaster.emit('join_room', {name: userName, uuid: roomName});
    } else {
      socketMaster.emit('create_room', {name: userName});
    }
  }

  updateRoomLen = () => {
    this.setState({
      roomNameLen: this.roomNameRef.current.value.length
    });
  }

  render() {
    const { roomNameLen } = this.state;

    return (
      <div className="App">
        <h1 className="uk-heading-medium uk-margin-medium-top uk-text-center">Avalon Game</h1>
        <div className="uk-container">
          <fieldset className="uk-fieldset">
            <div className="uk-margin">
              <div className="uk-form-label" style={{paddingBottom: '5px'}}>
                Room ID
                <span
                  data-uk-tooltip="Leave the Room ID empty to create a new room"
                  style={{marginLeft: '5px'}}
                >
                  <span data-uk-icon="question"></span>
                </span>
              </div>
              <div className="uk-form-controls">
                <input
                  className="uk-input"
                  type="text"
                  placeholder="Room ID"
                  onChange={this.updateRoomLen}
                  ref={this.roomNameRef}
                />
              </div>
            </div>
            <div className="uk-margin">
              <label className="uk-form-label">Username</label>
              <div className="uk-form-controls">
                <input
                  className="uk-input"
                  type="text"
                  placeholder="Username"
                  ref={this.userNameRef}
                />
              </div>
            </div>
            <div className="uk-margin">
              <button
                className="uk-button uk-button-primary uk-width-1-1 uk-margin-small-bottom"
                onClick={this.onJoinCreateRoom}
              >
                {roomNameLen > 0 ? 'Join Room' : 'Create Room'}
              </button>
            </div>
          </fieldset>
        </div>
      </div>
    );
  }
}

Login.contextType = AppContext;

export default Login;
