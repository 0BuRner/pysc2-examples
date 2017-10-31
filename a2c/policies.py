import numpy as np
import tensorflow as tf
from baselines.acktr.utils import conv, fc, dense, conv_to_fc, sample, kl_div
from baselines.common.distributions import make_pdtype
import baselines.common.tf_util as U
from pysc2.lib.features import actions

class CnnPolicy(object):

  def __init__(self, sess, ob_space, ac_space, nenv, nsteps, nstack, reuse=False):
    nbatch = nenv*nsteps
    nh, nw, nc = (32,32,1)
    ob_shape = (nbatch, nh, nw, nc * nstack)
    nact = 3 # 524
    # nsub3 = 2
    # nsub4 = 5
    # nsub5 = 10
    # nsub6 = 4
    # nsub7 = 2
    # nsub8 = 4
    # nsub9 = 500
    # nsub10 = 4
    # nsub11 = 10
    # nsub12 = 500

    # (64, 64, 13)
    # 80 * 24

    X = tf.placeholder(tf.uint8, ob_shape) #obs
    with tf.variable_scope("model", reuse=reuse):
      with tf.variable_scope("common", reuse=reuse):
        h = conv(tf.cast(X, tf.float32), 'c1', nf=16, rf=5, stride=1, init_scale=np.sqrt(2), pad="SAME") # ?, 32, 32, 16
        h2 = conv(h, 'c2', nf=32, rf=3, stride=1, init_scale=np.sqrt(2), pad="SAME") # ?, 32, 32, 32

      with tf.variable_scope("pi1", reuse=reuse):
        h3 = conv_to_fc(h2) # 131072
        h4 = fc(h3, 'fc1', nh=256, init_scale=np.sqrt(2)) # ?, 256
        pi_ = fc(h4, 'pi', nact, act=lambda x:x) # ( nenv * nsteps, 524) # ?, 524
        pi = tf.nn.softmax(pi_)

        vf_ = fc(h4, 'v', 1, act=lambda x:x) # ( nenv * nsteps, 1) # ?, 1
        vf = tf.clip_by_value(vf_, -10, 10)

      # with tf.variable_scope("sub3", reuse=reuse):
      #   pi_sub3 = fc(h4, 'pi_sub3', nsub3, act=lambda x:x) # ( nenv * nsteps, 2) # ?, 2
      # with tf.variable_scope("sub4", reuse=reuse):
      #   pi_sub4 = fc(h4, 'pi_sub4', nsub4, act=lambda x:x) # ( nenv * nsteps, 5) # ?, 5
      # with tf.variable_scope("sub5", reuse=reuse):
      #   pi_sub5 = fc(h4, 'pi_sub5', nsub5, act=lambda x:x) # ( nenv * nsteps, 10) # ?, 10
      # with tf.variable_scope("sub6", reuse=reuse):
      #   pi_sub6 = fc(h4, 'pi_sub6', nsub6, act=lambda x:x) # ( nenv * nsteps, 4) # ?, 4
      # with tf.variable_scope("sub7", reuse=reuse):
      #   pi_sub7_ = fc(pi, 'pi_sub7', nsub7, act=lambda x:x) # ( nenv * nsteps, 2) # ?, 2
      #   pi_sub7 = tf.nn.l2_normalize(pi_sub7_, 1)
      # with tf.variable_scope("sub8", reuse=reuse):
      #   pi_sub8_ = fc(pi, 'pi_sub8', nsub8, act=lambda x:x) # ( nenv * nsteps, 4) # ?, 4
      #   pi_sub8 = tf.nn.l2_normalize(pi_sub8_, 1)
      # with tf.variable_scope("sub9", reuse=reuse):
      #   pi_sub9_ = fc(pi, 'pi_sub9', nsub9, act=lambda x:x) # ( nenv * nsteps, 500) # ?, 500
      #   pi_sub9 = tf.nn.l2_normalize(pi_sub9_, 1)
      # with tf.variable_scope("sub10", reuse=reuse):
      #   pi_sub10_ = fc(pi, 'pi_sub10', nsub10, act=lambda x:x) # ( nenv * nsteps, 4) # ?, 4
      #   pi_sub10 = tf.nn.l2_normalize(pi_sub10_, 1)
      # with tf.variable_scope("sub11", reuse=reuse):
      #   pi_sub11_ = fc(pi, 'pi_sub11', nsub11, act=lambda x:x) # ( nenv * nsteps, 10) # ?, 10
      #   pi_sub11 = tf.nn.l2_normalize(pi_sub11_, 1)
      # with tf.variable_scope("sub12", reuse=reuse):
      #   pi_sub12_ = fc(pi, 'pi_sub12', nsub12, act=lambda x:x) # ( nenv * nsteps, 500) # ?, 500
      #   pi_sub12 = tf.nn.l2_normalize(pi_sub12_, 1)

      # vf = tf.nn.l2_normalize(vf_, 1)

      with tf.variable_scope("xy0", reuse=reuse):
        # 1 x 1 convolution for dimensionality reduction
        pi_xy0_ = conv(h2, 'xy0', nf=1, rf=1, stride=1, init_scale=np.sqrt(2)) # (? nenv * nsteps, 32, 32, 1)
        pi_xy0__ = conv_to_fc(pi_xy0_) # 32 x 32 => 1024
        pi_xy0 = tf.nn.softmax(pi_xy0__)

        #pi_xy0 =
        # TODO! bug!!!

        # tf.reshape(xy0,(None, 32 * 32))
        # pi_x0 = xy0[:,:,0,0] # ?, 32
        # x0 = sample(pi_x0) # ?,
        # pi_y0 = xy0[:,0,:,0] # ?, 32
        # y0 = sample(pi_y0) # ?,

      # with tf.variable_scope("xy1", reuse=reuse):
      #   xy1 = conv(h2, 'xy1', nf=1, rf=1, stride=1, init_scale=np.sqrt(2)) # (? nenv * nsteps, 32, 32, 1)
      #   pi_x1 = xy1[:,:,0,0] # ?, 32
      #   x1 = sample(pi_x1) # ?,
      #   pi_y1 = xy1[:,0,:,0] # ?, 32
      #   y1 = sample(pi_y1) # ?,
      #
      # with tf.variable_scope("xy2", reuse=reuse):
      #   xy2 = conv(h2, 'xy2', nf=1, rf=1, stride=1, init_scale=np.sqrt(2)) # (? nenv * nsteps, 32, 32, 1)
      #   pi_x2 = xy2[:,:,0,0] # ?, 32
      #   x2 = sample(pi_x2) # ?,
      #   pi_y2 = xy2[:,0,:,0] # ?, 32
      #   y2 = sample(pi_y2) # ?,

    v0 = vf[:, 0]
    a0 = sample(pi)
    self.initial_state = [] #not stateful

    def step(ob, *_args, **_kwargs):
      #obs, states, rewards, masks, actions, actions2, x1, y1, x2, y2, values
      _pi1, _xy0, _v = sess.run([pi,pi_xy0, v0], {X:ob})
      return _pi1, _xy0, _v, [] #dummy state

    def value(ob, *_args, **_kwargs):
      return sess.run(v0, {X:ob})

    self.X = X
    self.pi = pi
    # self.pi_sub3 = pi_sub3
    # self.pi_sub4 = pi_sub4
    # self.pi_sub5 = pi_sub5
    # self.pi_sub6 = pi_sub6
    # self.pi_sub7 = pi_sub7
    # self.pi_sub8 = pi_sub8
    # self.pi_sub9 = pi_sub9
    # self.pi_sub10 = pi_sub10
    # self.pi_sub11 = pi_sub11
    # self.pi_sub12 = pi_sub12
    self.pi_xy0 = pi_xy0
    # self.pi_y0 = pi_y0
    # self.pi_x1 = pi_x1
    # self.pi_y1 = pi_y1
    # self.pi_x2 = pi_x2
    # self.pi_y2 = pi_y2
    self.vf = vf
    self.step = step
    self.value = value

class GaussianMlpPolicy(object):
  def __init__(self, ob_dim, ac_dim):
    # Here we'll construct a bunch of expressions, which will be used in two places:
    # (1) When sampling actions
    # (2) When computing loss functions, for the policy update
    # Variables specific to (1) have the word "sampled" in them,
    # whereas variables specific to (2) have the word "old" in them
    ob_no = tf.placeholder(tf.float32, shape=[None, ob_dim*2], name="ob") # batch of observations
    oldac_na = tf.placeholder(tf.float32, shape=[None, ac_dim], name="ac") # batch of actions previous actions
    oldac_dist = tf.placeholder(tf.float32, shape=[None, ac_dim*2], name="oldac_dist") # batch of actions previous action distributions
    adv_n = tf.placeholder(tf.float32, shape=[None], name="adv") # advantage function estimate
    oldlogprob_n = tf.placeholder(tf.float32, shape=[None], name='oldlogprob') # log probability of previous actions
    wd_dict = {}
    h1 = tf.nn.tanh(dense(ob_no, 32, "h1", weight_init=U.normc_initializer(1.0), bias_init=0.0, weight_loss_dict=wd_dict))
    h2 = tf.nn.tanh(dense(h1, 64, "h2", weight_init=U.normc_initializer(1.0), bias_init=0.0, weight_loss_dict=wd_dict))
    mean_na = dense(h2, ac_dim, "mean", weight_init=U.normc_initializer(0.1), bias_init=0.0, weight_loss_dict=wd_dict) # Mean control output
    self.wd_dict = wd_dict
    self.logstd_1a = logstd_1a = tf.get_variable("logstd", [ac_dim], tf.float32, tf.zeros_initializer()) # Variance on outputs
    logstd_1a = tf.expand_dims(logstd_1a, 0)
    std_1a = tf.exp(logstd_1a)
    std_na = tf.tile(std_1a, [tf.shape(mean_na)[0], 1])
    ac_dist = tf.concat([tf.reshape(mean_na, [-1, ac_dim]), tf.reshape(std_na, [-1, ac_dim])], 1)
    sampled_ac_na = tf.random_normal(tf.shape(ac_dist[:,ac_dim:])) * ac_dist[:,ac_dim:] + ac_dist[:,:ac_dim] # This is the sampled action we'll perform.
    logprobsampled_n = - U.sum(tf.log(ac_dist[:,ac_dim:]), axis=1) - 0.5 * tf.log(2.0*np.pi)*ac_dim - 0.5 * U.sum(tf.square(ac_dist[:,:ac_dim] - sampled_ac_na) / (tf.square(ac_dist[:,ac_dim:])), axis=1) # Logprob of sampled action
    logprob_n = - U.sum(tf.log(ac_dist[:,ac_dim:]), axis=1) - 0.5 * tf.log(2.0*np.pi)*ac_dim - 0.5 * U.sum(tf.square(ac_dist[:,:ac_dim] - oldac_na) / (tf.square(ac_dist[:,ac_dim:])), axis=1) # Logprob of previous actions under CURRENT policy (whereas oldlogprob_n is under OLD policy)
    kl = U.mean(kl_div(oldac_dist, ac_dist, ac_dim))
    #kl = .5 * U.mean(tf.square(logprob_n - oldlogprob_n)) # Approximation of KL divergence between old policy used to generate actions, and new policy used to compute logprob_n
    surr = - U.mean(adv_n * logprob_n) # Loss function that we'll differentiate to get the policy gradient
    surr_sampled = - U.mean(logprob_n) # Sampled loss of the policy
    self._act = U.function([ob_no], [sampled_ac_na, ac_dist, logprobsampled_n]) # Generate a new action and its logprob
    #self.compute_kl = U.function([ob_no, oldac_na, oldlogprob_n], kl) # Compute (approximate) KL divergence between old policy and new policy
    self.compute_kl = U.function([ob_no, oldac_dist], kl)
    self.update_info = ((ob_no, oldac_na, adv_n), surr, surr_sampled) # Input and output variables needed for computing loss
    U.initialize() # Initialize uninitialized TF variables

  def act(self, ob):
    ac, ac_dist, logp = self._act(ob[None])
    return ac[0], ac_dist[0], logp[0]
