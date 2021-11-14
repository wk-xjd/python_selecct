from wkchat_app.clientapp import client_server_instance
from wkchat_app.svrapp import ServerApp
import multiprocessing


if __name__ == "__main__":
    pipe_r, pipe_s = multiprocessing.Pipe(False)
    pipe_r2, pipe_s2 = multiprocessing.Pipe(False)
    svr_pipe = (pipe_s, pipe_r2)
    client_pipe = (pipe_s2, pipe_r)

    sub_prco = multiprocessing.Process(target=client_server_instance, args=(client_pipe,))
    sub_prco.start()
    svr = ServerApp(svr_pipe)
    svr.run()
    sub_prco.join(3)






