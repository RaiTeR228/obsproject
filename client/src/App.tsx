import { useEffect, useState } from 'react'
import {login,me,register,type User} from './api'
import './App.css'

type Mode = "login" | "register"

function App() {
const [mode,setMode]= useState<Mode>("login")
const[email,setEmail] = useState("")
const[password,setPassword] = useState("")
const[user,setUser] = useState<string | null>(() => localStorage.getItem("token"))
const[error,setError] = useState<User | null>(null)
const[notice,setNotice] = useState("")
const[busy,setBusy] = useState("")
const[busy, setBusy] = useState(false)

useEffect(() => {
  if(!token) {setUser(null);return}
  me()
  .then(setUser)
  .catch(() =>{localStorage.removeItem('token');setToken(null);})
},[token])
const submit = async(e:React.FormEvent) => {
  e.preventDefault();
  setError("");setNotice("");setBusy(true);
  try{
    if (mode == "register"){
      await register(email,password);
      setNotice("Аккаунт создан входим")
    }
    const {access_token} = await login(email,password)
    localStorage.setItem("token",access_token);
    setToken(access_token);
  } catch(err){
    setError(err instanceof Error ? err.message:"случилось какаято хуйгя")
  }finally{
    setBusy(false)
  }
}  
const logout = () =>{
  localStorage.removeItem("token");
  setToken(null);setUser(null),setPassword();
}

if(token && !user) return <div> проверяем токен что вы не долбч</div>

  return (
    <>
      
    </>
  )
}

export default App
