3
F"_�"  �               @   s�   d dl Z d dlZd dlZd dlZd dlZd dlZd dlZd dlZd dlZd dl	Z	d dl
Z
d dlZd dlZdd� ZG dd� de�ZG dd� ded�Zd	d
� Zdd� Zedkr�e�  dS )�    Nc             C   s   t j| d �S )Ng    ��.A)�timeZsleep)�x� r   �imp_callback.py�<lambda>   s    r   c                   s    e Zd Zi Z� fdd�Z�  ZS )�	Singletonc                s,   | | j kr"tt| �j||�| j | < | j |  S )N)�
_instances�superr   �__call__)�cls�args�kwargs)�	__class__r   r   r
      s    
zSingleton.__call__)�__name__�
__module__�__qualname__r   r
   �__classcell__r   r   )r   r   r      s   r   c               @   s�   e Zd ZdZddd�Zeed�dd�Zed�d	d
�Zd dd�Z	d!dd�Z
ed�dd�Zdd� Zdd� Zdd� Zdd� Zdd� Zdd� ZdS )"�RequestImpressionz
config.ini� c             C   s   t j� | _| j|� d S )N)�configparserZConfigParser�config�
loadConfig)�self�dirnamer   r   r   �__init__    s    
zRequestImpression.__init__)�data�keyc             C   sd   | j |�}d}x,|D ]$}|t|�d t|| � d 7 }qW ||7 }tj� }|j|jd�� |j� S )Nr   �=�&�utf8)�ksort�str�hashlibZmd5�update�encodeZ	hexdigest)r   r   r   ZtmpStr�name�mr   r   r   �genSignature(   s    

$zRequestImpression.genSignature)r   c             C   sZ  t jjt jjt��d | j | _| jj| j� | jj� d | _	| j| j	 d | _
| j| j	 d | _| j| j	 d | _| j| j	 d | _| jj�  t| j�dkr�|| _t| j| j	 d �| _t| j| j	 d �| _t| j| j	 d	 �| _| j| j| j	 d
 �| _| j| j| j	 d �| _| jd tjdtj� � d | _| jd tjdtj� � d | _d S )N�/r   Zrequest_urlZ
secret_keyZdb_path�path�row_idZread_max_row�retry�	player_id�
ip_addressz
/req_fail_z%Y-%mz.logz/back_req_fail_z%Y-%m-%d)�osr)   �abspathr   �__file__�iniFiler   �readZsections�
configMame�
requestUrl�	secretKey�dbPath�strip�len�int�rowId�
readMaxRowr+   �getPlayerId�playerId�getIpAddress�	ipAddressr   �strftime�	localtime�failFile�	bakupFail)r   r   r   r   r   r   4   s"     
 zRequestImpression.loadConfigc             C   s2   |j �  t|�dkr.tjd�j� j � }t|�}|S )Nr   z/bin/DMS-broadsignID)r7   r8   r.   �popenr2   r9   )r   r=   r   r   r   r<   H   s
    zRequestImpression.getPlayerIdc             C   s<   |j �  t|�dkr8dd� tjtjtj�gD �d d }|S )Nr   c             S   s(   g | ] }|j d�|j� d |j� f�qS )�8.8.8.8�5   r   )rE   rF   )�connectZgetsockname�close)�.0�sr   r   r   �
<listcomp>U   s    z2RequestImpression.getIpAddress.<locals>.<listcomp>�   )r7   r8   �socketZAF_INETZ
SOCK_DGRAM)r   Zipr   r   r   r>   P   s    $zRequestImpression.getIpAddress)r   c                s   � fdd�t � j� �D �S )Nc                s   i | ]}� | |�qS r   r   )rI   �k)r   r   r   �
<dictcomp>Z   s    z+RequestImpression.ksort.<locals>.<dictcomp>)�sorted�keys)r   r   r   )r   r   r    Y   s    zRequestImpression.ksortc          
   C   s.   t |d��}|jtj|�d � W d Q R X dS )Nza+�
T)�open�write�json�dumps)r   r   ZfilePath�fr   r   r   �	writeFail]   s    zRequestImpression.writeFailc             C   sb   g }t jj| j�s|S t| jd��6}x|D ]}|jtj|�� q*W |jd� |j	�  W d Q R X |S )Nzr+r   )
r.   r)   �existsrB   rS   �appendrU   �loads�seek�truncate)r   �rowsrW   �liner   r   r   �readFailc   s    

zRequestImpression.readFailc             C   s�   | j � }x~|D ]v}d}xl|| jk r�| j|�}|dkrntd� |d7 }|| jkr�td| j|d� | j|| j� qtd| j|d� P qW qW d S )Nr   Fi � rL   zretry request row id:z request fail
z request sucess
)r`   r+   �request�usleep�printr:   rX   rC   )r   r^   �row�i�retr   r   r   �retryRequestr   s    


zRequestImpression.retryRequestc             C   s�   t j � }t| j�t|�| jd�}| j|| j�}||d< ||d< tj|�}ddi}yJt	j
| j||d�}|jdkr�|j� }td|� t|d	 �d
kr�dS dS W n
   dS d S )N)r,   r   r-   r   �tokenzContent-typezapplication/json)Zurlr   �headers��   zrequest response:�coder   TF)r   r!   r=   r9   r?   r'   r5   rU   rV   �requestsZpostr4   Zstatus_coderc   )r   r   �t�paramsrh   ri   �rZresponser   r   r   ra   �   s"    


zRequestImpression.requestc          	   C   s(   t | jd��}| jj|� W d Q R X d S )Nzw+)rS   r1   r   rT   )r   rW   r   r   r   �writeConfig�   s    zRequestImpression.writeConfigc             C   s�  t j| j�}t j|_|j� }| jdkrdd}|j|� t|j	� d �| j
 | _| jj| jdt| j�� d| j }|j|� t|j	� d �}tj|| j
 �}| j}�xtd|�D �]}d||| j
 | j
f }|j|� g }x@|j� D ]4}	t|	�}	| j|	d< | j|	d< |j|	� |	d | _q�W | jj| jdt| j�� |�s8q�d}xt|| jk �r�| j|�}
|
d	k�r�td
� |d7 }|| jk�r�td| j|d� | j|| j� ntd| j|d� P �q>W q�W | j�  |j�  |j�  d S )Nr   zESELECT  stat_id FROM monitor_stats_stat order by stat_id desc limit 1r*   zHselect count(stat_id) from monitor_stats_stat where stat_id > %s limit 1z�select stat_id , content_id as ad_copy_id , timestamp as imp_time , duration  from monitor_stats_stat where stat_id > %s limit %s , %sr,   r-   Zstat_idFi � rL   zretry request row id:z request failzrequest row id:z request sucess)�sqlite3rG   r6   ZRowZrow_factoryZcursorr:   �executer9   Zfetchoner;   r   �setr3   r!   �mathZceil�rangeZfetchall�dictr=   r?   rZ   r+   ra   rb   rc   rX   rB   rp   rH   )r   ZconnZcurZsqlZ	countRowsZpageSizeZmaxIdre   ZtmpDatard   rf   r   r   r   rr   �   sP    









zRequestImpression.executeN)r   )r   )r   )r   r   r   r1   r   rv   r!   r'   r   r<   r>   r    rX   r`   rg   ra   rp   rr   r   r   r   r   r      s   


	r   )�	metaclassc             C   s�   t jd|  dt jd�}|j}t|jj� �}|jj�  |j�  xJ|j	d�D ]<}t
jd|�}|rHt|d d �}|tj� krH||krHdS qHW dS )Nzps ax -o pid= -o args= |grep T)�shell�stdoutrR   z
(\d+) (.*)r   F)�
subprocess�Popen�PIPE�pidr!   ry   r2   rH   �wait�split�re�findallr9   r.   �getpid)r%   ZpsZpsPid�outputr_   �resr}   r   r   r   �checkProccess�   s    
r�   c              C   s�   t jjt jjt��\} }ttjd �s�y<t| �}t	dt
jdt
j� �d� |j�  |j�  t	d� W q� tk
r� } zW Y d d }~X q� tk
r� } zt	|� W Y d d }~X q�X nt	d� d S )Nr   zImpression Request Start z%Y-%m-%d %H:%M:%Sz RunzImpression Request run endzimp_callback runing now)r.   r)   r   r/   r0   r�   �sys�argvr   rc   r   r@   rA   rg   rr   �KeyboardInterrupt�	Exception)r   �_ZreqImp�er   r   r   �main�   s    r�   �__main__)r   r"   rU   rl   r   Zdatetimerq   rt   r.   rz   r�   r�   rM   rb   �typer   r   r�   r�   r   r   r   r   r   �<module>   s(    :