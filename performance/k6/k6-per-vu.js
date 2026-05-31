import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: Number(__ENV.VUS || 50),
  duration: __ENV.DURATION || '3s',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const LOGIN_PATH = __ENV.LOGIN_PATH || '/api/v1/auth/login/';
const TARGET_PATH = __ENV.TARGET_PATH || '/api/v1/estudiantes/';
const USERNAME = __ENV.USERNAME || 'admin_bd';
const PASSWORD = __ENV.PASSWORD || 'Password123!';

export default function () {
  const loginResponse = http.post(
    `${BASE_URL}${LOGIN_PATH}`,
    JSON.stringify({ username: USERNAME, password: PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  console.log(`Login status: ${loginResponse.status}`);
  console.log(`Login body: ${loginResponse.body}`);

  check(loginResponse, { 'login 200': (r) => r.status === 200 });
  if (loginResponse.status !== 200) {
    return;
  }

  const token = loginResponse.json('access');
  const apiResponse = http.get(`${BASE_URL}${TARGET_PATH}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  check(apiResponse, { 'api 200': (r) => r.status === 200 });
  sleep(1);
}
