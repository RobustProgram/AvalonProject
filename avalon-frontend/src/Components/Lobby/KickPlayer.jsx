import React from 'react';

export default function KickPlayer({kickPlayer, playerName}) {
  return (
    <button
      className="uk-icon-button uk-button-danger"
      data-uk-tooltip="Kick the user"
      data-uk-icon="ban"
      onClick={() => {
        kickPlayer(playerName);
      }}
    />
  )
}

