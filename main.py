from wkchat_app.serverpp import server_process_instance
from wkchat_app.connectionpp import ConnectionApp
import multiprocessing


if __name__ == "__main__":
    pipe_r, pipe_s = multiprocessing.Pipe(False)
    pipe_r2, pipe_s2 = multiprocessing.Pipe(False)
    connection_pipe = (pipe_s, pipe_r2)
    server_pipe = (pipe_s2, pipe_r)

    sub_prco = multiprocessing.Process(target=server_process_instance, args=(server_pipe,))
    sub_prco.start()
    svr = ConnectionApp(connection_pipe)
    svr.run()
    sub_prco.join(3)