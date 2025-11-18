import axios from 'axios';

export const pingBackend = async () => {
  const res = await axios.get('http://localhost:8000/ping');
  return res.data;
};
