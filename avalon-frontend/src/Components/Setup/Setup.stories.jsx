import { fn } from '@storybook/test';
import Setup from './Setup';
import AppContext from '../../AppContext';

export default {
  title: 'Pages/Setup',
  component: Setup,
  decorators: [
    (Story) => (
      <AppContext.Provider value={{ socketMaster: { emit: fn() } }}>
        <Story />
      </AppContext.Provider>
    ),
  ],
};

export const SetupPage = {};
