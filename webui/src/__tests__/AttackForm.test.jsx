import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AttackForm from '../components/AttackForm';
import React from 'react';

jest.mock('../utils/api', () => ({
  sendAttack: jest.fn(() => Promise.resolve({ status: 'ok' }))
}));

test('renders attack form and submits', async () => {
  const log = jest.fn();
  const { getByText } = render(<AttackForm log={log} />);
  fireEvent.click(getByText(/Launch Attack/i));
  expect(log).toHaveBeenCalled();
});
