import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ModeToggle from '../components/ModeToggle';
import React from 'react';

test('changing mode calls setMode', () => {
  const setMode = jest.fn();
  const { getByLabelText } = render(<ModeToggle mode="SAFE" setMode={setMode} />);
  fireEvent.change(getByLabelText(/Mode/i), { target: { value: 'AGGRESSIVE' } });
  expect(setMode).toHaveBeenCalledWith('AGGRESSIVE');
});
