import { useRouter } from "vue-router";

export function authGuard(to, from, next) {
  const token = localStorage.getItem("token");
  if (!token) {
    next("/auth");
  } else {
    next();
  }
}

export function adminGuard(to, from, next) {
  const isAdmin = localStorage.getItem("isAdmin") === "true";
  if (!isAdmin) {
    next("/");
  } else {
    next();
  }
}
