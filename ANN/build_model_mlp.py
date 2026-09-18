import tensorflow as tf

def build_model_feat(
    F=624,
    n_classes=5,
    hidden_units=(128, 64),
    norm="layernorm",          # "none" oder "layernorm"
    dropout=0.0,
    wd=1e-4,
    initializer="he_normal",
    lr=3e-4,
    leaky_alpha=0.1
):
    init = tf.keras.initializers.get(initializer)

    x_in = tf.keras.layers.Input(shape=(F,), name="feat")
    x = x_in
    if norm == "layernorm":
        x = tf.keras.layers.LayerNormalization()(x)

    for units in hidden_units:
        x = tf.keras.layers.Dense(
            units,
            activation=None,
            kernel_initializer=init,
            kernel_regularizer=tf.keras.regularizers.l2(wd) if wd and wd > 0 else None,
        )(x)
        x = tf.keras.layers.LeakyReLU(negative_slope=leaky_alpha)(x)
        if dropout and dropout > 0:
            x = tf.keras.layers.Dropout(dropout)(x)

    out = tf.keras.layers.Dense(n_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs=x_in, outputs=out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=[
            "accuracy",
            tf.keras.metrics.SparseCategoricalCrossentropy(name="ce"),
        ],
    )
    return model