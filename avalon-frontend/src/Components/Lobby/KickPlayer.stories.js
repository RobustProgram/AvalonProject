import { fn } from '@storybook/test';
import KickPlayer from './KickPlayer';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories#default-export
export default {
  title: 'Components/KickPlayer',
  component: KickPlayer,
  args: { kickPlayer: fn() },
};

export const Default = {
  args: { playerName: 'player1' },
};