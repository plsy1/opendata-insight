import { CanActivateFn } from '@angular/router';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { APP_PATHS } from '../app-paths';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);


  if (localStorage.getItem('loggedIn') === 'true') {
    return true;
  } else {
    router.navigate([APP_PATHS.login]);
    return false;
  }
};
